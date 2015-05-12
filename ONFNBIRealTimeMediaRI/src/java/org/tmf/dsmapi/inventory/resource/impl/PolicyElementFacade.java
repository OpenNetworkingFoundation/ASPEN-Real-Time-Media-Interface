/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.tmf.dsmapi.inventory.resource.impl;

import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import org.tmf.dsmapi.common.impl.AbstractFacade;
import org.tmf.dsmapi.inventory.resource.model.PolicyElement;

/**
 *
 * @author pierregauthier
 */
@Stateless
public class PolicyElementFacade extends AbstractFacade<PolicyElement> {
    @PersistenceContext(unitName = "ONFNBIRealTimeMediaRIPU")
    private EntityManager em;

    public PolicyElementFacade() {
        super(PolicyElement.class);
    }

    @Override
    protected EntityManager getEntityManager() {
        return em;
    }

}
