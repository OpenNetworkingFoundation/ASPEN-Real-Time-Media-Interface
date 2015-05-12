/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.onf.aspen.realtimemedia.impl;

import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import org.tmf.dsmapi.common.impl.AbstractFacade;
import org.onf.aspen.realtimemedia.model.SessionElement;

/**
 *
 * @author pierregauthier
 */
@Stateless
public class SessionElementFacade extends AbstractFacade<SessionElement> {
    @PersistenceContext(unitName = "ONFNBIRealTimeMediaRIPU")
    private EntityManager em;

    public SessionElementFacade() {
        super(SessionElement.class);
    }

    @Override
    protected EntityManager getEntityManager() {
        return em;
    }

}
