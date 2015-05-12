/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.onf.aspen.realtimemedia.model;

import javax.persistence.Embeddable;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */

@Embeddable
public class UserElement {
      private String name;
      private String id;
      private String realm;

    /**
     * @return the name
     */
    public String getName() {
        return name;
    }

    /**
     * @param name the name to set
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * @return the id
     */
    public String getId() {
        return id;
    }

    /**
     * @param id the id to set
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * @return the realm
     */
    public String getRealm() {
        return realm;
    }

    /**
     * @param realm the realm to set
     */
    public void setRealm(String realm) {
        this.realm = realm;
    }
    
}
